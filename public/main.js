
async function register(event) {
    // 阻止表單重新載入頁面，改用 fetch 呼叫後端 API。
    event.preventDefault();

    const form = event.currentTarget;
    const account = document.querySelector('#username');
    const nickname = document.querySelector('#nickname');
    const password = document.querySelector('#password');
    const confirmation = document.querySelector('#password-confirm');
    const message = document.querySelector('#message');
    const button = form.querySelector('button[type="submit"]');

    message.classList.remove('error');
    if (password.value !== confirmation.value) {
        message.textContent = 'Passwords do not match.';
        message.classList.add('error');
        return;
    }

    button.disabled = true;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                account: account.value,
                nickname: nickname.value,
                password: password.value
            })
        });

        const result = await response.json();
        message.textContent = result.message;

        if (result.success) {
            form.reset();
        } else {
            message.classList.add('error');
        }
    } catch (error) {
        // 網路錯誤或無法取得有效回應時顯示錯誤訊息。
        message.textContent = 'Registration failed. Please try again later.';
        message.classList.add('error');
    } finally {
        button.disabled = false;
    }
}

async function login(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const account = document.querySelector('#username');
    const password = document.querySelector('#password');
    const message = document.querySelector('#message');

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            account: account.value,
            password: password.value
        })
    });

    const result = await response.json();
    message.textContent = result.message;

    if (result.success) {
        window.location.href = '/message.html';
    } else {
        message.classList.add('error');
    }
}

async function setupSessionButton() {
    const button = document.querySelector('#logout-button');

    if (!button) {
        return;
    }

    try {
        const response = await fetch('/api/session');
        const session = await response.json();

        button.textContent = session.logged_in ? '登出' : '登入';

        button.addEventListener('click', async () => {
            if (!session.logged_in) {
                window.location.href = '/';
                return;
            }

            const logoutResponse = await fetch('/api/logout', {
                method: 'POST'
            });

            if (logoutResponse.ok) {
                window.location.reload();
            }
        });
    } catch (error) {
        button.textContent = '登入';
        button.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
}

document
    .querySelector('#register-form')
    ?.addEventListener('submit', register);

document
    .querySelector('#login-form')
    ?.addEventListener('submit', login);

setupSessionButton();
