import React from "react";
import styles from "../Styles/Buttons.module.css";

const Button = ({ children, margin, padding, className, onClick, ...rest }) => {
  return (
    <button
      {...rest}
      className={
        className &&
        className
          .split(" ")
          .map((item) => `${styles[item]}`)
          .join(" ")
      }
      onClick={onClick}
    >
      {children}
    </button>
  );
};

export default Button;
