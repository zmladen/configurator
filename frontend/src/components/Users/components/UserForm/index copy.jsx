import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Container from "../../../Container";
import Button from "../../../Button";
import ButtonGroup from "../../../ButtonGroup";
import { Form, Input, Select, TextArea } from "../../../Forms";
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
  const [defaultValues, setDefaultValues] = useState({});

  useEffect(() => {
    setLoader(true);
    const getUsers = async () => {
      const { data } = await fetchUsers();
      setUsers(data.users);
    };
    getUsers();
    setLoader(false);
    setUser(users.find((item) => item.id == id));

    setDefaultValues({
      firstname: user?.firstname,
      lastname: user?.lastname,
      email: user?.email,
      gender: user?.gender || "Male",
      username: user?.username,
      password: user?.password,
      user: user?.admin || "No",
      status: user?.status || "Active",
      mobileTelephone: user?.telephone?.mobile,
      officeTelephone: user?.telephone?.office || 123,
      about: user?.about || "",
    });
  }, [users.length, user]);

  const onSubmit = (data) => {
    user
      ? editUser(data)
          .then((response) => {
            alert(response.data);
            navigate(-1);
          })
          .catch(({ response }) => {
            alert(response.data);
          })
      : addUser(data)
          .then((response) => {
            alert(response.data);
            navigate(-1);
          })
          .catch(({ response }) => {
            alert(response.data);
          });
  };

  return (
    <div className={styles.Users}>
      <Container>
        <Form onSubmit={onSubmit} defaultValues={defaultValues}>
          <div>
            <Input label="First Name" name="firstname" required={true} />
            <Input label="Last Name" name="lastname" required={true} />
          </div>
          <Input label="Username" name="username" required={true} />
          <Input label="E-Mail" name="email" type="email" required={true} />
          <Input label="Password" name="password" required={true} />
          <Select label="Gender" name="gender" options={["Male", "Female"]} />
          <Select label="Admin?" name="admin" options={["Yes", "No"]} />
          <Select
            label="Status"
            defaultValue={user?.status ? "Active" : "Deactive"}
            name="status"
            options={["Active", "Deactive"]}
          />
          <Input label="Mobile Tel." name="mobileTelephone" required={true} />
          <Input label="Office Tel." name="officeTelephone" required={true} />

          <TextArea
            label="About"
            name="about"
            type="textarea"
            required={true}
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
        </Form>
      </Container>
    </div>
  );
}

export default UserForm;
