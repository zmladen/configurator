import React, {useState, useEffect} from "react";
import Container from "../components/Container";
import Logo from "../components/Logo";
import NavLink from "../components/Buttons/NavLink"
import { fetchMaterials } from "../services/materialsService";
import { fetchParts } from "../services/partsService";
import { fetchMachines } from "../services/machinesService";
import { useMaterials } from "../context/materialsContext";
import { useParts } from "../context/partsContext";
import { useMachine } from "../context/machineContext";

const WelcomePage = () => {
  const { materials, setMaterials } = useMaterials();
  const { parts, setParts } = useParts();
  const { machines, setMachines } = useMachine();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getMaterials = async () => {
      await fetchMaterials()
        .then(({ data }) => {
          setMaterials(data.data);
        })
        .catch(({ response }) => {
          console.log(response);
        });
    };

    const getParts = async () => {
      await fetchParts()
        .then(({ data }) => {
          setParts(data.data);
        })
        .catch(({ response }) => {
          console.log(response);
        });
    };

    const getMachines = async () => {
      await fetchMachines()
        .then(({ data }) => {
          setMachines(data.data);
        })
        .catch(({ response }) => {
          console.log(response);
        });
    };

    getMaterials();
    getParts();
    // getMachines();

    // setTimeout(() => setLoading(false), 1000);
    setLoading(false);
  }, [])

return (<>
    {/* <Logo src={"./images/passion-in-motion.svg"} alt="" /> */}

    <Container>
      <h3>BÜHLER MOTOR Configurator</h3>
      <p>Mit dem besonders benutzerfreundlich umgesetzten Drive Calculator lassen sich genau die FAULHABER Antriebssysteme aus Motor, Getriebe und Encoder ermitteln, die Sie für Ihre Projekte benötigen – und dann gezielt anfragen.</p>
      <p>Sie haben es eilig? Dann ist das Tool erst recht ideal für Sie. Mit wenigen Angaben wie Drehmoment und Drehzahl erfahren Sie schnell, welche FAULHABER Antriebslösungen grundsätzlich zu Ihrer Anwendung passen. Über Filter können Sie die mit den wichtigsten Parametern versehene Liste weiter reduzieren, bis Sie Ihre optimale Antriebslösung gefunden haben. Dabei hilft Ihnen eine Vergleichsfunktion, die bis zu drei Varianten mit ihren umfangreichen Produktdaten tabellarisch darstellt.</p>
      <p>Das FAULHABER Drive Calculator wird sukzessive weiter ausgebaut, schon heute berücksichtigt es zusätzlich die Änderungen der elektrischen Eigenschaften durch die Erwärmung des Motors bei der thermischen Berechnung. Auch kann man bestimmte Motorserien oder Motor-Getriebe-Kombinationen vorauswählen, um so die ideale Lösung mit den gewünschten Leistungsanforderungen zu erhalten. Sobald Sie die Ihren Wünschen entsprechende Antriebssysteme gefunden, können Sie diese direkt bei FAULHABER anfragen und ein Vertriebsingenieur wird sich umgehend mit Ihnen in Verbindung setzen.</p>
      <NavLink className="btn btn-dark btn-lg"  to="/configurator">Open Configurator</NavLink>
     <br/>
      <NavLink className="btn btn-dark btn-lg"  to="/users">Users Page</NavLink>
      <br/>
      <NavLink className="btn btn-dark btn-lg"  to="/machines">Machines Page</NavLink>

    </Container>
  </>)
}
export default WelcomePage;
