document.getElementById('signUpForm').addEventListener('submit', function(event) {
  event.preventDefault();

  var name = document.getElementById('name').value;
  var email = document.getElementById('email').value;
  var phone = document.getElementById('phone').value;
  var password = document.getElementById('password').value;

  if (name && email && phone && password) {
      if (password.length >= 6) {
          // Simulate a successful sign-up
          console.log('회원가입 성공!');
          // Here you can add actual sign-up logic, like sending data to the server
      } else {
          alert('비밀번호는 최소 6자이어야 합니다.');
      }
  } else {
      alert('모든 필드를 입력하십시오.');
  }
});
