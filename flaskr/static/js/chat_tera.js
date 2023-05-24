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

    fetch(generateResponseUrl, options)
      .then(response => response.json())
      .then(data => {
        console.log(data);
        // Accede a los campos del JSON de respuesta
        const response = data.response;
        const datetime = data.datetime;
        
        // Haz lo que necesites con los datos

        console.log(response, datetime);
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
                    <small>${datetime}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
        inputField.value = ""
      })
      .catch(error => {
        console.log('Error al obtener los datos JSON:', error);
      });
  }
});




// Crea un objeto con los datos a enviar en la solicitud POST


