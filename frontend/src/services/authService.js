import jwtDecode from "jwt-decode";
import http from "./httpServices";
import config from "../config.json";

const apiEndpoint = config.apiUrl + "/auth/";

export async function login(email, password) {
  try {
    const response = await http.post(apiEndpoint, { email, password });
    return jwtDecode(response.data.token);
    // return response.data;
  } catch (error) {
    alert({
      name: "Login Failed!",
      message: "Username and password are not correct.",
      toString: function () {
        return this.name + ": " + this.message;
      },
    });
    throw new Error("My error message: ");
  }
}
