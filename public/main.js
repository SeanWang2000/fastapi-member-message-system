
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

function formatMessageTime(value) {
    if (!value) {
        return '';
    }

    const date = new Date(String(value).replace(' ', 'T'));

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function deleteMessage(messageId, item) {
    if (!window.confirm('確定要刪除這則留言嗎？')) {
        return;
    }

    const button = item.querySelector('.delete-message-button');
    button.disabled = true;

    try {
        const response = await fetch(`/api/message/${messageId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || '留言刪除失敗');
        }

        await loadMessages();
    } catch (error) {
        window.alert(error.message || '留言刪除失敗，請稍後再試。');
        button.disabled = false;
    }
}

async function loadMessages() {
    const board = document.querySelector('#board');
    const count = document.querySelector('.message-count');

    if (!board) {
        return;
    }

    try {
        const response = await fetch('/api/message');

        if (!response.ok) {
            throw new Error('Failed to load messages');
        }

        const messages = await response.json();

        board.replaceChildren();
        count.textContent = `${messages.length} 則留言`;

        if (messages.length === 0) {
            const emptyMessage = document.createElement('p');
            emptyMessage.className = 'board-status';
            emptyMessage.textContent = '目前還沒有留言';
            board.appendChild(emptyMessage);
            return;
        }

        messages.forEach((message) => {
            const item = document.createElement('article');
            item.className = 'message-item';

            const meta = document.createElement('div');
            meta.className = 'message-meta';

            const author = document.createElement('span');
            author.className = 'message-author';
            author.textContent = message.nick_name;

            const time = document.createElement('time');
            time.dateTime = message.create_time;
            time.textContent = formatMessageTime(message.create_time);

            const content = document.createElement('p');
            content.className = 'message-content';
            content.textContent = message.content;

            meta.append(author, time);
            if (message.can_delete) {
                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-message-button';
                deleteButton.type = 'button';
                deleteButton.textContent = '刪除';
                deleteButton.addEventListener('click', () => {
                    deleteMessage(message.id, item);
                });
                meta.appendChild(deleteButton);
            }
            item.append(meta, content);
            board.appendChild(item);
        });
    } catch (error) {
        board.replaceChildren();
        const errorMessage = document.createElement('p');
        errorMessage.className = 'board-status error';
        errorMessage.textContent = '留言載入失敗，請稍後再試。';
        board.appendChild(errorMessage);
    }
}

async function publishMessage() {
    const content = document.querySelector('#content');
    const button = document.querySelector('#publish-button');
    const message = document.querySelector('#publish-message');
    const value = content.value.trim();

    message.classList.remove('error');

    if (!value) {
        message.textContent = '請輸入留言內容';
        message.classList.add('error');
        return;
    }

    button.disabled = true;
    message.textContent = '';

    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: value
            })
        });

        const result = await response.json();
        message.textContent = result.message;

        if (result.success) {
            content.value = '';
            await loadMessages();
        } else {
            message.classList.add('error');
        }
    } catch (error) {
        message.textContent = '留言發布失敗，請稍後再試。';
        message.classList.add('error');
    } finally {
        button.disabled = false;
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
loadMessages();

document
    .querySelector('#publish-button')
    ?.addEventListener('click', publishMessage);
