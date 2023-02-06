import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/parts/";

export function fetchParts() {
  return http.get(apiEndpoint);
}

export default {
  fetchParts,
};
