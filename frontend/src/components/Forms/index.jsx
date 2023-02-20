import React, { useState, useEffect, useRef } from "react";
import styles from "./Styles/Forms.module.css";

export const SideBySide = ({ children }) => {
  const [child1, child2] = React.Children.toArray(children);

  return (
    <div className={styles.SideBySide}>
      {child1}
      {child2}
    </div>
  );
};

export const SideBySideLeft = ({ children }) => {
  const [child1, child2] = React.Children.toArray(children);

  return (
    <div className={styles.SideBySide}>
      {child1}
      {child2}
    </div>
  );
};

export const DragAndDrop = ({ name, label, setValue, getValues, register, errors, required, type, validationSchema, ...rest }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const dragAreaRef = useRef(null);
  const [fileNames, setFileNames] = useState([]);
  let counter = 0;

  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragging(true);
    counter++;
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    counter === 0 && setIsDragging(false);
    counter--;
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    setValue(name, e.dataTransfer.files);
    setFileNames([...e.dataTransfer.files].map((item) => item.name));
  };

  const handleFileChange = (e) => {
    setFileNames([...e.target.files].map((item) => item.name));
    setValue(name, e.target.files);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div ref={dragAreaRef} className={`${styles.dropzone} ${isDragging ? styles.isDragging : ""}`} onClick={handleClick} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>
      <span className={styles.prompt}>{fileNames.length ? `${fileNames.length} files selected` : "Drag and drop a file here or click to select a file"}</span>
      <input
        id={"name"}
        name={name}
        type={"file"}
        className={styles.fileInput}
        {...register(name, validationSchema)}
        ref={fileInputRef}
        multiple="multiple"
        {...rest}
        onChange={(e) => {
          handleFileChange(e);
        }}
      />
      {errors && errors[name]?.type === "required" && <span className="error">{errors[name]?.message}</span>}
    </div>
  );
};

export const FileInput = ({ name, label, register, errors, required, type, validationSchema, children, ...rest }) => {
  const [fileName, setFileName] = useState();

  const handleFileChange = (e) => {
    setFileName(e.target.files[0].name);
  };

  return (
    <div className={styles.FileInput}>
      <label htmlFor={name}>
        {fileName ? fileName : label}
        {validationSchema && "*"}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        {...register(name, validationSchema)}
        onChange={(e) => {
          handleFileChange(e);
        }}
        {...rest}
      />
      {fileName && children && children}
      {errors && errors[name]?.type === "required" && <span className="error">{errors[name]?.message}</span>}
    </div>
  );
};

export const Input = ({ name, label, register, errors, required, type, validationSchema, ...rest }) => (
  <div className={styles.Input}>
    <label htmlFor={name}>
      {label}
      {validationSchema && "*"}
    </label>
    <input id={name} name={name} type={type} {...register(name, validationSchema)} {...rest} />
    {errors && errors[name]?.type === "required" && <span className="error">{errors[name]?.message}</span>}
  </div>
);

export const TextArea = ({ name, label, register, errors, required, type, validationSchema, ...rest }) => (
  <div className={styles.TextArea}>
    <label htmlFor={name}>
      {label}
      {required && "*"}
    </label>
    <textarea id={name} name={name} type={type} {...rest} {...register(name, validationSchema)} />
    {errors && errors[name]?.type === "required" && <span className="error">{errors[name]?.message}</span>}
  </div>
);

export const Select = ({ name, label, register, errors, required, type, validationSchema, options, ...rest }) => (
  <div className={styles.Select}>
    <label htmlFor={name}>
      {label}
      {required && "*"}
    </label>

    <select id={name} name={name} type={type} {...rest} {...register(name, validationSchema)}>
      {options.map((value, index) => (
        <option key={index} value={value}>
          {value}
        </option>
      ))}
    </select>

    {errors && errors[name]?.type === "required" && <span className="error">{errors[name]?.message}</span>}
  </div>
);
