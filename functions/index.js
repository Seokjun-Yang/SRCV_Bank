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

        // Step 2: 계좌 정보 가져오기
        const accountResponse = await axios.get(
            `https://testapi.openbanking.or.kr/v2.0/user/me?user_seq_no=${user_seq_no}`,
            { headers: { Authorization: `Bearer ${access_token}` } }
        );

        const accountList = accountResponse.data.res_list;

        // 계좌 정보가 있을 경우 저장할 첫 번째 계좌 정보
        let account_info = {};
        if (accountList && accountList.length > 0) {
            const recentAccount = accountList[0];
            account_info = {
                fintech_use_num: recentAccount.fintech_use_num,
                bank_name: recentAccount.bank_name,
                account_num_masked: recentAccount.account_num_masked,
                balance_amt: 100000,  // 기본 잔액 설정
                available_amt: 90000, // 출금 가능 금액 설정
                transactions: [
                    {
                        amount: 0,
                        date: 'No Date',
                        description: 'no transactions',
                        type: '정보 없음',
                        balance: 0
                    }
                ]
            };
        }

        // Firebase에 저장할 사용자 정보 업데이트
        const userRef = admin.database().ref(`/users/${user_seq_no}`);
        const userSnapshot = await userRef.once('value');
        const userData = userSnapshot.val() || {};

        const updatedUserData = {
            ...userData,
            token: {
                access_token,
                refresh_token
            },
            account: account_info,
            user_info: userData.user_info || {}
        };

        // Firebase에 데이터 저장
        await userRef.update(updatedUserData);

        // 클라이언트로 user_seq_no 응답
        res.status(200).json({
            message: '토큰 및 계좌 정보가 성공적으로 저장되었습니다.',
            user_seq_no: user_seq_no
        });
    } catch (error) {
        console.error('Error during token exchange or fetching account info:', error.message);
        res.status(500).json({ error: '오류가 발생했습니다.', details: error.message });
    }
});
