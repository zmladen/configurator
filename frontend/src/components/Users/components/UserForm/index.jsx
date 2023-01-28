import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import Container from "../../../Container";
import Button from "../../../Button";
import ButtonGroup from "../../../ButtonGroup";
import { Input, TextArea, Select } from "../../../Forms";
import {
  fetchUsers,
  addUser,
  editUser,
} from "../../../../services/userService";
import styles from "./Styles/UserForm.module.css";

function UserForm(props) {
  const navigate = useNavigate();
  const [loader, setLoader] = useState(false);
  const [users, setUsers] = useState([]);
  const [user, setUser] = useState({});
  const [id, setId] = useState(useParams().id);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      firstname: user?.firstname,
      lastname: user?.lastname,
      email: user?.email,
      gender: user?.gender || "Male",
      username: user?.username,
      password: user?.password,
      user: user?.admin || "No",
      status: user?.status || "Active",
      mobileTelephone: user?.telephone?.mobile,
      officeTelephone: user?.telephone?.office,
      about: user?.about || "",
    },
  });

  useEffect(() => {
    setLoader(true);
    const getUsers = async () => {
      const { data } = await fetchUsers();
      setUsers(data.users);
    };
    getUsers();
    setLoader(false);
    setUser(users.find((item) => item.id == id));

    reset({
      ...user,
      mobileTelephone: user.telephone.mobile,
      officeTelephone: user.telephone.mobile,
    });
  }, [users.length, user]);

  const onSubmit = (data) => {
    console.log(data);
    // user
    //   ? editUser(data)
    //       .then((response) => {
    //         alert(response.data);
    //         navigate(-1);
    //       })
    //       .catch(({ response }) => {
    //         alert(response.data);
    //       })
    //   : addUser(data)
    //       .then((response) => {
    //         alert(response.data);
    //         navigate(-1);
    //       })
    //       .catch(({ response }) => {
    //         alert(response.data);
    //       });
  };

  return (
    <div className={styles.UserForm}>
      <Container>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.TwoFields}>
            <Input label="First Name" name="firstname" register={register} />
            <Input label="Last Name" name="lastname" register={register} />
          </div>

          <div className={styles.TwoFields}>
            <Input
              label="Username"
              name="username"
              // errors={errors}
              register={register}
              // validationSchema={{
              //   required: "Todo deadline is required",
              // }}
            />
            <Input label="Password" name="password" register={register} />
          </div>

          <Input label="E-Mail" name="email" type="email" register={register} />

          <Select
            label="Gender"
            name="gender"
            options={["Male", "Female"]}
            register={register}
          />

          <div className={styles.TwoFields}>
            <Select
              label="Admin?"
              name="admin"
              options={["Yes", "No"]}
              register={register}
            />
            <Select
              label="Status"
              defaultValue={user?.status ? "Active" : "Deactive"}
              name="status"
              options={["Active", "Deactive"]}
              register={register}
            />
          </div>

          <div className={styles.TwoFields}>
            <Input
              label="Mobile Tel."
              name="mobileTelephone"
              register={register}
            />
            <Input
              label="Office Tel."
              name="officeTelephone"
              register={register}
            />
          </div>

          <TextArea
            label="About"
            name="about"
            type="textarea"
            errors={errors}
            register={register}
            placeholder="Enter your text..."
          />

          <ButtonGroup>
            {user ? (
              <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20">
                Edit Changes
              </Button>
            ) : (
              <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20">
                Add New User
              </Button>
            )}

            <Button
              className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20"
              type="button"
              onClick={() => navigate(-1)}
            >
              Cancel
            </Button>
          </ButtonGroup>
        </form>
      </Container>
    </div>
  );
}

export default UserForm;
