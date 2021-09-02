import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1s', target: 40 },
   // { duration: '1m', target: 1 },
    { duration: '1m', target: 40 },
  ],
};

export default function () {
  let zeta_server_url // Fill the appropriate location where ZETA is deployed
  let res = http.get(`http://${zeta_server_url}/authentication?name=test-service&capabilities=cpu&expiry=1`);
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
