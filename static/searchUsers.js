const searchInput = document.getElementById('twitter');
const optionsWrapper = document.querySelector('.options-wrapper');
const options = document.getElementById('options');

let timeoutId;

searchInput.addEventListener('input', event => {
    clearTimeout(timeoutId);
    const query = event.target.value.trim();
    if (query.length >= 3) {
        timeoutId = setTimeout(() => {
            const query = {
                username: event.target.value.trim()
            };
            const json = JSON.stringify(query)
            axios.post(`${window.origin}/search-twitter-accounts`, json, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => {
                    const users = response.data.data;
                    console.log("usersFounded: ", users);
                    if (users.length > 0) {
                        options.innerHTML = '';
                        users.forEach(user => {
                            const option = document.createElement('div');
                            option.classList.add('option');
                            const imgWrapper = document.createElement('div');
                            imgWrapper.classList.add('img-wrapper');
                            const img = document.createElement('img');
                            img.src = user.profile_image_url;
                            img.alt = user.name;
                            imgWrapper.appendChild(img);
                            option.appendChild(imgWrapper);
                            const textWrapper = document.createElement('div');
                            textWrapper.classList.add('text-wrapper');
                            const name = document.createElement('span');
                            name.classList.add('name');
                            name.textContent = user.name;
                            const screenName = document.createElement('span');
                            screenName.classList.add('screen-name');
                            screenName.textContent = `@${user.screen_name}`;
                            textWrapper.appendChild(name);
                            textWrapper.appendChild(screenName);
                            option.appendChild(textWrapper);
                            option.addEventListener('click', () => {
                                searchInput.value = user.screen_name;
                                optionsWrapper.style.display = 'none';
                            });
                            options.appendChild(option);
                        });
                        optionsWrapper.style.display = 'block';
                    } else {
                        optionsWrapper.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error(error);
                    optionsWrapper.style.display = 'none';
                });
        }, 300);
    } else {
        optionsWrapper.style.display = 'none';
    }
});

document.addEventListener('click', event => {
    if (!searchInput.contains(event.target)) {
        optionsWrapper.style.display = 'none';
    }
});