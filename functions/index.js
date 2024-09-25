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

        // 사용자 정보 조회
        const userRef = admin.database().ref(`/users/${user_seq_no}`);
        await userRef.set({
            access_token,
            refresh_token,
            user_seq_no
        });

        // Step 3: 사용자 계좌 목록 조회
        const accountListResponse = await axios.get('https://testapi.openbanking.or.kr/v2.0/user/me', {
            headers: {
                Authorization: `Bearer ${access_token}`,
            },
            params: {
                user_seq_no: user_seq_no,
            },
        });

        const accountList = accountListResponse.data.res_list;

        // Firebase에 저장할 계좌 데이터 준비
        const accountsData = {};

        // Step 4: 각 계좌 초기 잔액 및 거래 내역 추가
        accountList.forEach(account => {
            const balance_amt = 100000;  // 초기 잔액 100,000원
            const available_amt = Math.floor(balance_amt * 0.9); // 출금 가능 금액: 잔액의 90%

            accountsData[account.fintech_use_num] = {
                fintech_use_num: account.fintech_use_num,
                account_holder_name: account.account_holder_name,
                account_num_masked: account.account_num_masked,
                balance_amt,
                available_amt,
                transactions: { initial: "No transactions yet" } // transactions을 빈 객체 대신 초기 상태를 저장
            };
        });

        // Step 5: Firebase에 계좌 목록 및 초기 잔액 저장
        await userRef.child('accounts').set(accountsData);

        res.status(200).json({ message: '토큰과 계좌 목록이 성공적으로 저장되었습니다.' });
    } catch (error) {
        console.error('Error during token exchange or account fetching:', error.message);
        res.status(500).json({ error: '오류가 발생했습니다.', details: error.message });
    }
});
