import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/materials/";

export function fetchMaterials() {
  return http.get(apiEndpoint);
}

export default {
  fetchMaterials,
};
