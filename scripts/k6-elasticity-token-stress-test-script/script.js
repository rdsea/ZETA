import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1s', target: 25 },
    { duration: '1m', target: 25 },
    { duration: '1m', target: 25 },
  ],
};

export default function () {
  let res = http.get('http://195.148.21.10:5000/elasticity?name=test-service&expiry=12&auth_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE2MjcwNzE1NDIsIm5iZiI6MTYyNzAzNTU0MiwiYXVkIjpbInRlZmE6dGVzdC1zZXJ2aWNlIl0sInR5cGUiOiJhdXRoX3Rva2VuIiwiY2YiOiJjcHUsZ3B1In0.Q-sGc-1CrmQtyfLeVuppHlDv2DQTl577QAEB6Z24CSEPoZtyw_5CIPyHaOa5Txw8lccrAaO2hRbKX21_MMv0bQ&claims=cpu&value=12&target=edge-inference-server');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
