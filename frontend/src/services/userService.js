import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/users/";


export function editUser(user) {
  return http.put(apiEndpoint, user);
}

export function addUser(user) {
  return http.post(apiEndpoint, user);
}

export function deleteUser(user) {
  // console.log(user)
  return http.delete(apiEndpoint, {data:user});
}

export function fetchUsers(user) {
  return http.get(apiEndpoint);
}

export default {
  addUser,
  fetchUsers,
  deleteUser,
  editUser
};
