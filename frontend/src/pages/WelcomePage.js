import React from "react";
import Container from "../components/Container";
import Logo from "../components/Logo";
import NavLink from "../components/NavLink";
const WelcomePage = () => (
  <>
    {/* <Logo src={"./images/passion-in-motion.svg"} alt="" /> */}

    <Container>
      <h3>Our motto: Fast Forward in all areas</h3>
      <p>
        Fast, flexible, authentic, personal, working as a team to create
        customized drive solutions.
      </p>

      <h3>Analyse Customer Requirements</h3>
      <p style={{ fontSize: "1em" }}>
        Yes you can do this here in a matter of seconds.
      </p>
      <NavLink to="/configurator">Open Configurator</NavLink>
      <NavLink to="/users">Users Page</NavLink>
    </Container>
  </>
);
export default WelcomePage;
