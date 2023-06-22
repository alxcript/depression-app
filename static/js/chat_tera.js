const inputField = document.getElementById('query-input');
const generateResponseUrl = document.getElementById('query-input').getAttribute('data-url');

inputField.addEventListener('keydown', event => {
  if (event.key === 'Enter') {
    event.preventDefault(); // Evita el comportamiento predeterminado de la tecla "Enter"

    const query = inputField.value;

    const data = {
      query: query
    };

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    };

    console.log(query); // Puedes modificar esto según tus necesidades

    document.getElementById('chat-go').innerHTML += `
      <div class="row justify-content-end text-right mb-4">
        <div class="col-auto">
          <div class="card bg-gradient-primary text-white">
            <div class="card-body p-2">
              <p class="mb-1">
                ${query}<br>
              </p>
              <div class="d-flex align-items-center justify-content-end text-sm opacity-6">
                <i class="fa fa-check-double mr-1 text-xs" aria-hidden="true"></i>
                <small>${new Date().toLocaleString()}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    inputField.value = ''
    

    const tabla = document.getElementById('chat-go');
    const newElements = tabla.querySelectorAll('.row');
    const lastElement = newElements[newElements.length - 2];
    lastElement.scrollIntoView({ behavior: 'smooth' });

    const typingAnimationHTML = `
      <div class="row justify-content-start mb-4 typing-animation-row">
        <div class="col-auto">
          <div class="card">
            <div class="card-body p-2">
              <div class="typing-animation">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
              
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('chat-go').innerHTML += typingAnimationHTML;

    const typingAnimationRow = document.querySelector('.typing-animation-row');
    const typingAnimation = typingAnimationRow.querySelector('.typing-animation');
    const dots = typingAnimation.querySelectorAll('.dot');
    
    animateTyping(dots);

    setTimeout(() => {
      fetch(generateResponseUrl, options)
        .then(response => response.json())
        .then(data => {
          const response = data.response;
          const datetime = data.datetime;

          console.log(response); // Puedes modificar esto según tus necesidades

          document.getElementById('chat-go').innerHTML += `
            <div class="row justify-content-start mb-4">
              <div class="col-auto">
                <div class="card">
                  <div class="card-body p-2">
                    <p class="mb-1">
                      ${response}
                    </p>
                    <div class="d-flex align-items-center text-sm opacity-6">
                      <i class="far fa-clock mr-1" aria-hidden="true"></i>
                      <small>${datetime}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `;

          const tabla = document.getElementById('chat-go');
          const newElements = tabla.querySelectorAll('.row');
          const lastElement = newElements[newElements.length - 1];
          lastElement.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
          console.log('Error al obtener los datos JSON:', error);
        })
        .finally(() => {
          typingAnimationRow.remove();
        });

      ;
      typingAnimationRow.remove();
    }, 2000); // Tiempo de espera de 3 segundos antes de enviar la solicitud fetch
  }
});

function animateTyping(dots) {
  let index = 0;
  const interval = setInterval(() => {
    dots[index].classList.add('active');
    index = (index + 1) % dots.length;
    dots[index].classList.remove('active');
  }, 500);
  return interval;
}
