document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var email = document.getElementById('email').value;
  var password = document.getElementById('password').value;

  if (email && password) {
      // Simulate a successful login
      console.log('로그인 성공!');
      // Here you can add actual login logic, like sending data to the server
  } else {
      alert('이메일과 비밀번호를 입력하십시오.');
  }
});
