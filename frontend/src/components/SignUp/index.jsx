import React, { useState } from "react";
import Button from "../../components/Button";
import styles from "./Styles/SignUp.module.css";
import { Form, Input } from "../../components/Forms";

function SignUp(props) {
  const [loader, setLoader] = useState(false);

  const onSubmit = async (data) => {
    setLoader(true);
    console.log(data);
    setLoader(false);
  };

  return (
    <div className={styles.SignUp}>
      <h1>Sign Up</h1>
      <Form onSubmit={onSubmit}>
        <Input label="First Name" name="firstName" required={true} />
        <Input label="Last Name" name="lastName" required={true} />
        <Input label="E-Mail" name="email" required={true} />
        <Input label="Password" name="password" required={true} />
        <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20">Sign Up</Button>
      </Form>
    </div>
  );
}

export default SignUp;
