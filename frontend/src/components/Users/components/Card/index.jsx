import React, { useState, useEffect } from "react";
import styles from "./styles/Card.module.css";
import { UserIcon } from "@heroicons/react/24/solid";

function Card({ user }) {
  console.log(user);
  return (
    <div className={styles.Chard}>
      <div className={styles.Image}>
        <UserIcon />
      </div>
      <div className={styles.Wrapper}>
        <div className={styles.Title}>
          <h4>{`${user.lastname}, ${user.firstname}`}</h4>
        </div>

        <div className={styles.Content}>
          <p>
            <span>E-Mail: </span>
            {user.email}
          </p>
          <p>
            <span>Tel.: </span>
            {user.telephone}
          </p>
          <p>
            <span>Address: </span>
            {user.address}
          </p>

          {/* <p>{`Password: ${user.password}`}</p> */}
        </div>
      </div>
    </div>
  );
}

export default Card;
