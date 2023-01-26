import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import { Form, Input } from "../../components/Forms";
import { useUser } from "../../context/userContext";
import styles from "./Styles/LogIn.module.css";
import { login } from "../../services/authService";

function LogIn(props) {
  const [loader, setLoader] = useState(false);
  const { setUser } = useUser();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setLoader(true);
    const response = await login(data.email, data.password);
    setUser({ ...response });
    setLoader(false);
    navigate(-1);
  };

  return (
    <div className={styles.SignUp}>
      <h1>Log In</h1>
      <Form onSubmit={onSubmit}>
        <Input label="E-Mail" name="email" required={true} />
        <Input label="Password" name="password" type="password" required={true} />
        <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20">Log In</Button>
      </Form>
    </div>
  );
}

export default LogIn;
