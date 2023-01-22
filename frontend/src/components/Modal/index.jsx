import React, { useState } from "react";
import styles from "./styles/Modal.module.css";
const Modal = ({ children, title, isOpen, onClose }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    isOpen = false;
  };

  return (
    <div>
      {/* <button onClick={openModal}>Open Modal</button> */}
      {isOpen && (
        <div className={styles.modal}>
          <div
            className={styles["modal-content"]}
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles["modal-header"]}>
              {title || <span />}
              <span className={styles["close-button"]} onClick={onClose}>
                &times;
              </span>
            </div>
            <div className={styles["modal-body"]}>{children}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Modal;
