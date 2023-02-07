import React from "react";
import Container from "../components/Container";
import Logo from "../components/Logo";
import NavLink from "../components/NavLink";
const WelcomePage = () => (
  <>
    {/* <Logo src={"./images/passion-in-motion.svg"} alt="" /> */}

    <Container>
      <h3>BÜHLER MOTOR Configurator</h3>
      <p>Mit dem besonders benutzerfreundlich umgesetzten Drive Calculator lassen sich genau die FAULHABER Antriebssysteme aus Motor, Getriebe und Encoder ermitteln, die Sie für Ihre Projekte benötigen – und dann gezielt anfragen.</p>
      <p>Sie haben es eilig? Dann ist das Tool erst recht ideal für Sie. Mit wenigen Angaben wie Drehmoment und Drehzahl erfahren Sie schnell, welche FAULHABER Antriebslösungen grundsätzlich zu Ihrer Anwendung passen. Über Filter können Sie die mit den wichtigsten Parametern versehene Liste weiter reduzieren, bis Sie Ihre optimale Antriebslösung gefunden haben. Dabei hilft Ihnen eine Vergleichsfunktion, die bis zu drei Varianten mit ihren umfangreichen Produktdaten tabellarisch darstellt.</p>
      <p>Das FAULHABER Drive Calculator wird sukzessive weiter ausgebaut, schon heute berücksichtigt es zusätzlich die Änderungen der elektrischen Eigenschaften durch die Erwärmung des Motors bei der thermischen Berechnung. Auch kann man bestimmte Motorserien oder Motor-Getriebe-Kombinationen vorauswählen, um so die ideale Lösung mit den gewünschten Leistungsanforderungen zu erhalten. Sobald Sie die Ihren Wünschen entsprechende Antriebssysteme gefunden, können Sie diese direkt bei FAULHABER anfragen und ein Vertriebsingenieur wird sich umgehend mit Ihnen in Verbindung setzen.</p>
      <NavLink className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20"  to="/configurator">Open Configurator</NavLink>
     <br/>
      <NavLink className="btn btn-dark btn-lg br-25 pt-10 pb-10 pl-20 pr-20"  to="/users">Users Page</NavLink>
    </Container>
  </>
);
export default WelcomePage;
