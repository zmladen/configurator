import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/machines/";
const apiEndpointScrapPDF = config.apiUrl + "/machines/scrapPDF/";

export function fetchMachines() {
  return http.get(apiEndpoint);
}

export function scrapPDF(data) {
  return http.post(apiEndpointScrapPDF, data);
}

export default {
  fetchMachines,
  scrapPDF,
};
