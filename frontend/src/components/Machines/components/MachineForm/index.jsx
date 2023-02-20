import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import Container from "../../../Container";
import Button from "../../../Buttons/Button";
import ButtonFileInput from "../../../Buttons/ButtonFileInput";
import ButtonGroup from "../../../Buttons/ButtonGroup";
import { useMachine } from "../../../../context/machineContext";
import { Input, Select, SideBySide, DragAndDrop } from "../../../Forms";
import Modal from "../../../Modal";
import styles from "./Styles/MachineForm.module.css";
import { scrapPDF } from "../../../../services/machinesService";
// import DragAndDrop from "../../../Buttons/DragAndDrop";

function NewMachine(props) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loader, setLoader] = useState(false);
  const [scrapData, setScrapData] = useState(false);
  const [initialValues, setInitialData] = useState({});
  const modalForm = useForm({});

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    getValues,
    formState: { errors },
  } = useForm({});

  useEffect(() => {
    reset({ ...initialValues });
  }, [initialValues]);

  const onSubmit = async (data) => {
    console.log("Form 2 submitted");
    console.log(data);
  };

  return (
    <div>
      <Container>
        <Modal title={"Initialize from PDF or continue..."} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <form
            id="my-form"
            onSubmit={modalForm.handleSubmit((data) => {
              setInitialData(scrapData[data.type]);
              setIsModalOpen(false);
            })}
          >
            <Select label="Type" name="type" options={Object.keys(scrapData)} register={modalForm.register} />
            <ButtonGroup>
              <Button className={"btn btn-dark btn-lg pt-5 pb-5"} form="my-form">
                Ok
              </Button>
            </ButtonGroup>
          </form>
        </Modal>
        <form id="parent-form" className={styles.MachineForm} onSubmit={handleSubmit(onSubmit)}>
          <h3>General Data</h3>
          <Input label="Type" name="Type" register={register} errors={errors} />

          <h3>Nominal Load Characteristics</h3>
          <SideBySide>
            <Input label="Rated voltage" name="Rated voltage" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Rated power" name="Rated power" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Rated torque" name="Rated torque" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Rated speed" name="Rated speed" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Rated current" name="Rated current" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <h3>No-Load Characteristics</h3>
          <SideBySide>
            <Input label="No load speed" name="No load speed" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="No load current" name="No load current" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <h3>Stall Characteristics</h3>
          <SideBySide>
            <Input label="Stall torque" name="Stall torque" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Stall current" name="Stall current" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <h3>Performance Characteristics</h3>
          <SideBySide>
            <Input label="max. Output power" name="max. Output power" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="max. Constant torque" name="max. Constant torque" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <h3>Motor Paramenters</h3>
          <SideBySide>
            <Input label="Weight" name="Weight" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Rotor inertia" name="Rotor inertia" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Terminal resistance" name="Terminal resistance" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Inductance" name="Inductance" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Mech. time constant" name="Mech. time constant" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Electr. time constant" name="Electr. time constant" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Speed regulation constant" name="Speed regulation constant" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Torque constant" name="Torque constant" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Thermal resistance" name="Thermal resistance" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Thermal time constant" name="Thermal time constant" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <SideBySide>
            <Input label="Axial play" name="Axial play" register={register} errors={errors} validationSchema={{ required: "required!" }} />
            <Input label="Direction of rotation" name="Direction of rotation" register={register} errors={errors} validationSchema={{ required: "required!" }} />
          </SideBySide>

          <h3>Files</h3>
          <DragAndDrop label="Drag and Drop Files Here" name="files" register={register} errors={errors} setValue={setValue} getValues={getValues} />
        </form>

        <ButtonGroup>
          <Button className="btn btn-dark btn-lg" type="submit" form="parent-form">
            Add Machine
          </Button>

          <ButtonFileInput
            className="btn btn-dark btn-lg"
            label="Load From PDF"
            onFileSelected={async (file) => {
              setLoader(true);
              const formData = new FormData();
              formData.append("pdf", file);

              await scrapPDF(formData)
                .then(({ data }) => {
                  setLoader(false);
                  setScrapData(data.data);
                  Object.keys(data.data).length > 1 && setIsModalOpen(true);
                })
                .catch(({ response }) => {
                  console.log(response);
                  setLoader(false);
                });
            }}
          />

          <Button className="btn btn-dark btn-lg" type="button" onClick={() => navigate(-1)}>
            Cancel
          </Button>
        </ButtonGroup>
      </Container>
    </div>
  );
}

export default NewMachine;
