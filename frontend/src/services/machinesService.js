import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/machines/";

export function fetchMachines() {
  return http.get(apiEndpoint);
}

export default {
  fetchMachines,
};
