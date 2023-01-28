import React, { useEffect } from "react";
import { useForm, useFormContext } from "react-hook-form";
import styles from "./Styles/Forms.module.css";

export function Form({ defaultValues, children, onSubmit }) {
  const {
    handleSubmit,
    register,
    reset,
    formState: { errors },
  } = useForm({ defaultValues: { ...defaultValues } });

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

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

export const ConnectForm = ({ children }) => {
  const methods = useFormContext();

  return children({ ...methods });
};

// export const Group = () => (
//   <ConnectForm>
//     {({ register }) => <input {...register("deepNestedInput")} />}
//   </ConnectForm>
// );

export function Group({ children, register, ...rest }) {
  return (
    <ConnectForm>
      <div>{React.cloneElement(children, { ref: { register }, ...rest })}</div>
    </ConnectForm>
  );
}

export function Input({ register, name, label, errors, ...rest }) {
  return (
    <>
      <label className={styles.Input}>{label}</label>
      <input {...register(name)} {...rest} />
      {errors?.[name] && <p>This field is required</p>}
    </>
  );
}

export function TextArea({ register, name, label, errors, ...rest }) {
  return (
    <>
      <label className={styles.Input}>{label}</label>
      <textarea {...register(name)} {...rest} />
      {errors?.[name] && <p>This field is required</p>}
    </>
  );
}

export function Select({ register, options, name, label, ...rest }) {
  return (
    <>
      <label>{label}</label>
      <select className={styles.Select} {...register(name)} {...rest}>
        {options.map((value, index) => (
          <option key={index} value={value}>
            {value}
          </option>
        ))}
      </select>
    </>
  );
}
