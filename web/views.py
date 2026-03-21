from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db.models.expressions import result
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView
from rest_framework_simplejwt.tokens import RefreshToken

from creators.models import Creator
from creators.services import create_or_update_creator_stripe_data
from payments.models import Payment
from payments.services import stripe_create_checkout_session
from posts.models import Post
from posts.tasks import notify_subscribers_about_new_post
from subscriptions.models import Subscription
from users.models import PhoneLoginCode, TelegramLinkToken
from users.serializers import RequestCodeSerializer, VerifyCodeSerializer
from web.forms import CreateForm, PostForm, RequestCodeForm, VerifyCodeForm

User = get_user_model()


class HomeView(ListView):
    """Главная страница"""

    model = Post
    template_name = "web/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        return (
            Post.objects.filter(is_published=True).select_related("creator").order_by("-published_at", "-created_at")
        )


class CreatorListView(ListView):
    """Список всех авторов"""

    model = Creator
    template_name = "web/creators.html"
    context_object_name = "creators"

    def get_queryset(self):
        return Creator.objects.all().select_related("user").order_by("display_name")


class CreatorDetailView(DetailView):
    """Детальная страница автора"""

    model = Creator
    template_name = "web/creator_detail.html"
    context_object_name = "creator"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        creator = self.object

        posts = Post.objects.filter(creator=creator, is_published=True).order_by("-published_at", "-created_at")

        context["posts"] = posts

        context["is_subscribed"] = False

        if self.request.user.is_authenticated:
            context["is_subscribed"] = Subscription.objects.filter(
                user=self.request.user, creator=creator, status=Subscription.Status.ACTIVE
            ).exists()

        return context


class PostDetailView(DetailView):
    """Детальная страница поста"""

    model = Post
    template_name = "web/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related("creator")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.object
        can_view_full = True

        if post.is_paid:
            can_view_full = False

            if self.request.user.is_authenticated:
                if post.creator.user_id == self.request.user.id:
                    can_view_full = True
                else:
                    can_view_full = Subscription.objects.filter(
                        user=self.request.user, creator=post.creator, status=Subscription.Status.ACTIVE
                    ).exists()

        context["can_view_full"] = can_view_full

        return context


def login_view(request):
    """Регистрация пользователя(вводит номер телефона и получает код)"""

    if request.user.is_authenticated:
        return redirect("web_dashboard")

    form = RequestCodeForm(request.POST)

    if request.method == "POST":
        if form.is_valid():
            serializer = RequestCodeSerializer(
                data={"phone": form.cleaned_data["phone"]}
            )

            if serializer.is_valid():
                result = serializer.save()

                request.session["auth_phone"] = form.cleaned_data["phone"]

                if result["delivery_method"] == "telegram":
                    messages.success(request, "Код отправлен в Telegram.")
                else:
                    messages.success(request, "Код отправлен. Проверьте консоль сервера.")

                return redirect("web_verify_code")

            messages.error(request, "Ошибка при отправке кода.")
        else:
            messages.error(request, "Проверьте номер телефона.")

    return render(request, "web/login.html", {"form": form})


def verify_code_view(request):
    """Пользователь вводит код и входит в систему"""

    if request.user.is_authenticated:
        return redirect("web_dashboard")

    initial_phone = request.session.get("auth_phone", "")
    form = VerifyCodeForm(request.POST or None, initial={"phone": initial_phone})

    if request.method == "POST":
        if form.is_valid():
            serializer = VerifyCodeSerializer(
                data={
                    "phone": form.cleaned_data["phone"],
                    "code": form.cleaned_data["code"],
                }
            )

            if serializer.is_valid():
                result = serializer.save()
                user = result["user"]

                login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                request.session["jwt_access"] = result["access"]
                request.session["jwt_refresh"] = result["refresh"]

                messages.success(request, "Вход выполнен успешно.")
                return redirect("web_dashboard")

            messages.error(request, "Неверный код или номер телефона.")
        else:
            messages.error(request, "Заполните форму корректно.")

    return render(request, "web/verify_code.html", {"form": form})


@login_required
def logout_view(request):
    """Выход из аккаунта"""

    logout(request)
    request.session.pop("jwt_access", None)
    request.session.pop("jwt_refresh", None)

    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("web_home")


@login_required
def subscribe_creator_view(request, creator_id: int):
    creator = get_object_or_404(Creator, id=creator_id)

    if not creator.stripe_price_id:
        return render(
            request,
            "web/error.html",
            {"message": "У автора пока не настроена оплата Stripe."},
            status=400,
        )

    success_url = request.build_absolute_uri(reverse("web_payment_success"))
    cancel_url = request.build_absolute_uri(reverse("web_payment_cancel"))

    session = stripe_create_checkout_session(
        price_id=creator.stripe_price_id,
        success_url=success_url,
        cancel_url=cancel_url,
        user_id=request.user.id,
        creator_id=creator.id,
    )

    # Сохраняем payment в БД
    Payment.objects.create(
        user=request.user,
        creator=creator,
        stripe_session_id=session["id"],
        status=Payment.Status.PENDING,
    )

    return redirect(session["url"])


def payment_success_view(request):
    """Просто страница успешной оплаты."""
    return render(request, "web/payment_success.html")


def payment_cancel_view(request):
    """Страница отмены оплаты."""
    return render(request, "web/payment_cancel.html")


@login_required
def dashboard_view(request):
    """Личный кабинет пользователя."""

    subscriptions = Subscription.objects.filter(user=request.user).select_related("creator").order_by("-created_at")

    creator_profile = getattr(request.user, "creator_profile", None)

    my_posts = []
    if creator_profile:
        my_posts = Post.objects.filter(creator=creator_profile).order_by("-created_at")[:5]

    telegram_link = None
    if not request.user.telegram_chat_id:
        token = TelegramLinkToken.objects.filter(user=request.user, is_used=False).order_by("-created_at").first()

        if not token:
            import secrets
            token = TelegramLinkToken.objects.create(
                user=request.user,
                token=secrets.token_hex(16),
                is_used=False,
            )

        telegram_link = f"https://t.me/followandpay_bot?start={token.token}"

    context = {
        "subscriptions": subscriptions,
        "creator_profile": creator_profile,
        "my_posts": my_posts,
        "telegram_link": telegram_link,
    }
    return render(request, "web/dashboard.html", context)


@login_required
def my_subscriptions_view(request):
    """Отдельная страница с подписками пользователя."""

    subscriptions = Subscription.objects.filter(user=request.user).select_related("creator").order_by("-created_at")

    return render(
        request,
        "web/my_subscriptions.html",
        {"subscriptions": subscriptions},
    )


@login_required
def my_posts_view(request):
    """Страница со своими постами автора."""

    creator = getattr(request.user, "creator_profile", None)
    if not creator:
        return render(
            request,
            "web/error.html",
            {"message": "У вас ещё нет профиля автора."},
            status=400,
        )

    posts = Post.objects.filter(creator=creator).order_by("-created_at")

    return render(
        request,
        "web/my_posts.html",
        {"posts": posts, "creator": creator},
    )


@login_required
def creator_form_view(request):
    """Создание/редактирование профиля автора"""

    creator = getattr(request.user, "creator_profile", None)

    if request.method == "POST":
        form = CreateForm(
            data=request.POST,
            instance=creator,
        )

        if form.is_valid():
            creator_obj = form.save(commit=False)
            creator_obj.user = request.user
            creator_obj.save()

            create_or_update_creator_stripe_data(creator_obj)

            messages.success(request, "Профиль автора сохранен.")
            return redirect("web_dashboard")
    else:
        form = CreateForm(instance=creator)

    return render(
        request,
        "web/creator_form.html",
        {"form": form, "creator": creator},
    )


@login_required
def post_create_view(request):
    """Создание нового поста"""

    creator = getattr(request.user, "creator_profile", None)

    if not creator:
        return render(request, "web/error.html", {"message": "Сначала создайте профиль автора."}, status=400)
    form = PostForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.creator = creator
        post.save()

        messages.success(request, "Пост успешно создан.")
        return redirect("web_my_posts")

    return render(request, "web/post_form.html", {"form": form, "is_edit": False})


@login_required
def post_update_view(request, post_id: int):
    """Редактирование поста"""

    creator = getattr(request.user, "creator_profile", None)
    if not creator:
        return render(
            request,
            "web/error.html",
            {"message": "Сначала создайте профиль автора."},
            status=400,
        )

    post = get_object_or_404(Post, id=post_id, creator=creator)
    form = PostForm(request.POST or None, instance=post)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Пост успешно обновлён.")
        return redirect("web_my_posts")

    return render(request, "web/post_form.html", {"form": form, "is_edit": True, "post": post})


@login_required
def post_publish_view(request, post_id: int):
    """Публикация поста"""

    creator = getattr(request.user, "creator_profile", None)
    if not creator:
        return render(
            request,
            "web/error.html",
            {"message": "Сначала создайте профиль автора."},
            status=400,
        )

    post = get_object_or_404(Post, id=post_id, creator=creator)
    post.is_published = True

    from django.utils import timezone

    post.published_at = timezone.now()
    post.save(update_fields=["is_published", "published_at"])

    notify_subscribers_about_new_post.delay(post.id)

    messages.success(request, "Пост успешно опубликован.")
    return redirect("web_my_posts")
