import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Container from "../../../Container";
import Button from "../../../Button";
import styles from "./Styles/User.module.css";
import { useUser } from "../../../../context/userContext";
import { EnvelopeIcon, PhoneIcon, DevicePhoneMobileIcon } from "@heroicons/react/24/solid";

<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
  <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 006 3.75v16.5a2.25 2.25 0 002.25 2.25h7.5A2.25 2.25 0 0018 20.25V3.75a2.25 2.25 0 00-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3" />
</svg>;

function User(props) {
  const navigate = useNavigate();
  const { users, setUsers } = useUser();
  const [user, setUser] = useState({});
  const [id, setId] = useState(useParams().id);

  useEffect(() => {
    setUser(users.find((item) => item.id === id));
  }, [id]);

  return (
    <Container>
      <div className={styles.User}>
        <header className={styles.header}>
          <img src={"/images/maleProfile.png"} className={styles.profileImg} alt="profile" />
          <h1 className={styles.name}>{`${user?.firstname}, ${user?.lastname}`}</h1>
        </header>
        <section className={styles.about}>
          <h2 className={styles.sectionHeader}>About</h2>
          <p>I am a software developer with 5 years of experience.</p>
        </section>
        <section className={styles.contact}>
          <h2 className={styles.sectionHeader}>Contact</h2>
          <p>
            <EnvelopeIcon /> {user?.email}
          </p>
          <p>
            <PhoneIcon />: {user?.telephone?.office}
          </p>
          <p>
            <DevicePhoneMobileIcon />: {user?.telephone?.mobile}
          </p>
        </section>
      </div>

      <Button className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20" type="button" onClick={() => navigate(-1)}>
        Go Back
      </Button>
    </Container>
  );
}

export default User;
