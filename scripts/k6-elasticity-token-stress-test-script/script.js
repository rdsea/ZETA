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
  let zeta_server_url // Fill the appropriate location where ZETA is deployed
  let auth_token // Get a fresh auth token and put it here
  let res = http.get(`http://${zeta_server_url}/elasticity?name=test-service&expiry=12&auth_token=${auth_token}&claims=cpu&value=12&target=edge-inference-server`);
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}
