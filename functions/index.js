const functions = require('firebase-functions');
const admin = require('firebase-admin');
const axios = require('axios');
const qs = require('qs');

// Firebase 초기화
if (!admin.apps.length) {
    admin.initializeApp();
}

exports.authCallback = functions.https.onRequest(async (req, res) => {
    const authCode = req.query.code;
    const clientId = 'd79bfcd3-1b00-4f8b-8ffc-aa06a317801c';
    const clientSecret = 'aedf07ac-4c32-4a81-a363-0a5a8418e74e';
    const redirectUri = 'https://us-central1-bank-a752e.cloudfunctions.net/authCallback';

    try {
        // Step 1: Access Token 발급
        const tokenResponse = await axios.post(
            'https://testapi.openbanking.or.kr/oauth/2.0/token',
            qs.stringify({
                code: authCode,
                client_id: clientId,
                client_secret: clientSecret,
                redirect_uri: redirectUri,
                grant_type: 'authorization_code',
            }),
            {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            }
        );

        const { access_token, refresh_token, user_seq_no } = tokenResponse.data;

        // Firebase에 저장할 사용자 토큰 업데이트
        const userRef = admin.database().ref(`/users/${user_seq_no}`);
        const userSnapshot = await userRef.once('value');
        const userData = userSnapshot.val() || {};

        // 사용자 토큰 저장
        const updatedUserData = {
            ...userData,
            access_token,
            refresh_token,
            user_seq_no
        };

        // Firebase에 업데이트된 사용자 토큰 정보 저장
        await userRef.update(updatedUserData);

        res.status(200).json({ message: '토큰이 성공적으로 저장되었습니다.' });
    } catch (error) {
        console.error('Error during token exchange:', error.message);
        res.status(500).json({ error: '오류가 발생했습니다.', details: error.message });
    }
});
