import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/users/";

export function register(user) {
  return http.post(apiEndpoint, {
    firstname: user.firstname,
    lastname: user.lastname,
    email: user.email,
    password: user.password,
  });
}

export function fetchUsers(user) {
  return http.get(apiEndpoint);
}

export default {
  register,
  fetchUsers,
};
