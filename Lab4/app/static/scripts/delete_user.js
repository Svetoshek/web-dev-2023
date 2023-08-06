// Получаем доступ к элементу "модальное окно" для удаления пользователя
let deleteUserModal = document.querySelector('#deleteUser')

// Назначаем обработку события, когда окно появляется (show.bs.modal, см. Bootstrap5)
deleteUserModal.addEventListener('show.bs.modal', function(event) {
    let form = document.querySelector('form');
    form.action = event.relatedTarget.dataset.url;
    let userLogin = document.querySelector('#userLogin');
    userLogin.innerHTML = event.relatedTarget.closest('tr').querySelector('#fullName').textContent;
});
