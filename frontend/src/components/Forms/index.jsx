import React, { useEffect } from "react";
import { useForm, useFormContext } from "react-hook-form";
import styles from "./Styles/Forms.module.css";

export const Input = ({
  name,
  label,
  register,
  errors,
  required,
  type,
  validationSchema,
  ...rest
}) => (
  <div className={styles.Input}>
    <label htmlFor={name}>
      {label}
      {required && "*"}
    </label>
    <input
      id={name}
      name={name}
      type={type}
      {...rest}
      {...register(name, validationSchema)}
    />
    {errors && errors[name]?.type === "required" && (
      <span className="error">{errors[name]?.message}</span>
    )}
  </div>
);

export const TextArea = ({
  name,
  label,
  register,
  errors,
  required,
  type,
  validationSchema,
  ...rest
}) => (
  <div className={styles.Input}>
    <label htmlFor={name}>
      {label}
      {required && "*"}
    </label>
    <textarea
      id={name}
      name={name}
      type={type}
      {...rest}
      {...register(name, validationSchema)}
    />
    {errors && errors[name]?.type === "required" && (
      <span className="error">{errors[name]?.message}</span>
    )}
  </div>
);

export const Select = ({
  name,
  label,
  register,
  errors,
  required,
  type,
  validationSchema,
  options,
  ...rest
}) => (
  <div className={styles.Input}>
    <label htmlFor={name}>
      {label}
      {required && "*"}
    </label>

    <select
      className={styles.Select}
      id={name}
      name={name}
      type={type}
      {...rest}
      {...register(name, validationSchema)}
    >
      {options.map((value, index) => (
        <option key={index} value={value}>
          {value}
        </option>
      ))}
    </select>

    {errors && errors[name]?.type === "required" && (
      <span className="error">{errors[name]?.message}</span>
    )}
  </div>
);
