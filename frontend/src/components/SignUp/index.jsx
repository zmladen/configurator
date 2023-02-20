import React, { useState } from "react";
import { useForm } from "react-hook-form";
import Button from "../Buttons/Button";
import styles from "./Styles/SignUp.module.css";
import { Input } from "../../components/Forms";

function SignUp(props) {
  const [loader, setLoader] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({});

  const onSubmit = async (data) => {
    setLoader(true);
    console.log(data);
    setLoader(false);
  };

  return (
    <div className={styles.SignUp}>
      <h1>Sign Up</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Input label="First Name" name="firstName" register={register} />
        <Input label="Last Name" name="lastName" register={register} />
        <Input label="E-Mail" name="email" register={register} />
        <Input label="Password" name="password" register={register} />
        <Button className="btn btn-dark btn-lg">Sign Up</Button>
      </form>
    </div>
  );
}

export default SignUp;
