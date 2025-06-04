document.addEventListener('DOMContentLoaded', function() {
	const signinBtn = document.getElementById('signinBtn');
	const signupBtn = document.getElementById('signupBtn');
	const signinForm = document.getElementById('signinForm');
	const signupForm = document.getElementById('signupForm');
	const successMessage = document.querySelector('.success');


	signinForm.classList.add('active');

	signinBtn.addEventListener('click', () => {
			signinForm.classList.add('active');
			signupForm.classList.remove('active');
			signinBtn.parentElement.classList.add('signin-active');
			signinBtn.parentElement.classList.remove('signin-inactive');
			signupBtn.parentElement.classList.add('signup-inactive');
			signupBtn.parentElement.classList.remove('signup-active');
	});

	signupBtn.addEventListener('click', () => {
			signupForm.classList.add('active');
			signinForm.classList.remove('active');
			signupBtn.parentElement.classList.add('signup-active');
			signupBtn.parentElement.classList.remove('signup-inactive');
			signinBtn.parentElement.classList.add('signin-inactive');
			signinBtn.parentElement.classList.remove('signin-active');
	});
	signupForm.addEventListener('submit', function(event) {
		event.preventDefault(); 
	
		successMessage.style.display = 'block'; 
});
});
