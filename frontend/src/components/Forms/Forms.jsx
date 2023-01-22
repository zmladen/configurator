import React from "react";
import { useForm } from "react-hook-form";
import styles from "./Styles/Forms.module.css";

export function Form({ defaultValues, children, onSubmit }) {
  const { handleSubmit, register } = useForm({ defaultValues });

  return (
    <form className={styles.Form} onSubmit={handleSubmit(onSubmit)}>
      {Array.isArray(children)
        ? children.map((child) => {
            return child.props.name
              ? React.createElement(child.type, {
                  ...{
                    ...child.props,
                    register,
                    key: child.props.name,
                  },
                })
              : child;
          })
        : children}
    </form>
  );
}

export function Input({ register, name, label, ...rest }) {
  return (
    <>
      <label>{label}</label>
      <input {...register(name)} {...rest} />
    </>
  );
}

export function Select({ register, options, name, ...rest }) {
  return (
    <select {...register(name)} {...rest}>
      {options.map((value) => (
        <option value={value}>{value}</option>
      ))}
    </select>
  );
}
