import os
import math


class controlcircuit(object):
    """This model calculates the electronic losses of the ECU."""

    def __init__(self, data):

        self.data = data
        self.cc = self.data["Used"]
        self.temperature = self.cc.get("Temperature (C)", 25)
        self.controlAlgorithm = self.cc["Control Algorithm"]["name"]
        self.Nshunts = self.cc["Parts"]["Current Shunts"]["Total Number"]
        self.Ntransistors = self.cc["Parts"]["Power Transistors"]["Total Number"]
        self.tr = self.cc["Parts"]["Power Transistors"]["Parameters"]["Rise Time MOSFET (s)"]
        self.tf = self.cc["Parts"]["Power Transistors"]["Parameters"]["Fall Time MOSFET (s)"]
        self.ImaxTransistorRMS = self.cc["Parts"]["Power Transistors"]["Parameters"]["Maximal Current Rating RMS (A)"]
        self.pwmFrequency = self.cc["Parts"]["Microcontroller"]["PWM Frequency (Hz)"]
        self.dutyCycle = self.cc["Parts"]["Microcontroller"]["Duty Cycle (%)"]
        self.Vdc = self.cc["Power Source"]["Supply Voltage (V)"]
        self.phaseAdvance = self.cc["Phase Advance Angle (deg.el.)"]
        self.Cp = (self.cc["Parts"]["Intermediate Circuit Capacitors"]["Capacitance (F)"] * self.cc["Parts"]["Intermediate Circuit Capacitors"]["Total Number"])
        self.Ls = (self.cc["Parts"]["Intermediate Circuit Inductances"]["Inductance (H)"] * self.cc["Parts"]["Intermediate Circuit Inductances"]["Total Number"])

    def getLosses(self, Isource, Irms, Iripple):
        return {
            "Total Losses (W)": self.Psource(Isource) + self.Pcontacts(Irms) + self.PpowerStage(Isource, Irms, Iripple),
            "Source Losses (W)": self.Psource(Isource),
            "Power Stage Losses (W)": self.PpowerStage(Isource, Irms, Iripple),
            "Contacts Losses (W)": self.Pcontacts(Irms),
            "Reverse Pole Protections Losses (W)": self.MOSFET_rpp_losses(Isource),
            "Capacitor Conduction Losses (W)": self.COND_conduction_losses(Iripple),
            "Inductance Conduction Losses (W)": self.IND_conduction_losses(Isource),
            "Shunt Conduction Losses (W)": self.SHUNT_conduction_losses(Irms),
            "PCB Conduction Losses (W)": self.PCB_conduction_losses(Irms),
            "Microcontroller Losses (W)": self.uC_losses(),
            "LDO Losses (W)": self.LDO_losses(),
            "Power Transistors Conduction Losses (W)": self.MOSFET_conduction_losses(Irms),
            "Power Transistors Switching Losses (W)": self.MOSFET_switching_losses(Irms),
            "Source Resistance Losses (W)": self.Source_Resistance_losses(Isource),
            "Contact Resistance Losses (W)": self.Contact_Resistance_losses(Irms),
            "Number of Shunts": self.Nshunts,
            "Number of Transistors": self.Ntransistors,
        }

    @property
    def Rtransistor(self):
        Tc_Rtransistor = self.cc["Parts"]["Power Transistors"]["Parameters"][
            "Resistance Tc (%/C)"
        ]
        Rtransistor = self.cc["Parts"]["Power Transistors"]["Parameters"]["Rdson (Ohm)"]
        return Rtransistor * (1 + Tc_Rtransistor / 100 * (self.temperature - 25))

    @property
    def Rsource(self):
        Tc_Rsource = self.cc["Power Source"]["Resistance Tc (%/C)"]
        Rsource = self.cc["Power Source"]["Inner Resistance (Ohm)"]
        return Rsource * (1 + Tc_Rsource / 100 * (self.temperature - 25))

    @property
    def Rcable(self):
        Tc_Rcable = self.cc["Cable Resistance"]["Resistance Tc (%/C)"]
        Rcable = self.cc["Cable Resistance"]["Resistance (Ohm)"]
        return Rcable  # * (1 + Tc_Rcable / 100 * (self.temperature - 25))

    @property
    def Rshunt(self):
        Tc_shunt = self.cc["Parts"]["Current Shunts"]["Resistance Tc (%/C)"]
        Rshunt = (self.cc["Parts"]["Current Shunts"]["Resistance (Ohm)"] * self.cc["Parts"]["Current Shunts"]["Total Number"])
        return Rshunt * (1 + Tc_shunt / 100 * (self.temperature - 25))

    @property
    def Rpcb(self):
        Tc_pcb = self.cc["Parts"]["PCB"]["Resistance Tc (%/C)"]
        Rpcb = self.cc["Parts"]["PCB"]["Conduction Resistance (Ohm)"]
        return Rpcb * (1 + Tc_pcb / 100 * (self.temperature - 25))

    @property
    def Rind(self):
        Tc_Ind = self.cc["Parts"]["Intermediate Circuit Inductances"]["Resistance Tc (%/C)"]
        Rind = (self.cc["Parts"]["Intermediate Circuit Inductances"]["Resistance (Ohm)"] * self.cc["Parts"]["Intermediate Circuit Inductances"]["Total Number"])
        return Rind * (1 + Tc_Ind / 100 * (self.temperature - 25))

    @property
    def Rrpp(self):
        Tc_rpp = self.cc["Parts"]["Reverse Polarity Protections"]["Parameters"]["Resistance Tc (%/C)"]
        Rrpp = (
            self.cc["Parts"]["Reverse Polarity Protections"]["Parameters"][
                "Rdson (Ohm)"
            ]
            * self.cc["Parts"]["Reverse Polarity Protections"]["Total Number"]
        )
        return Rrpp * (1 + Tc_rpp / 100 * (self.temperature - 25))

    @property
    def Rcond(self):
        Tc_Cond = self.cc["Parts"]["Intermediate Circuit Capacitors"][
            "Resistance Tc (%/C)"
        ]
        Rcond = (
            self.cc["Parts"]["Intermediate Circuit Capacitors"]["Resistance (Ohm)"]
            / self.cc["Parts"]["Intermediate Circuit Capacitors"]["Total Number"]
        )
        return Rcond * (1 + Tc_Cond / 100 * (self.temperature - 25))

    def PpowerStage(self, Isource, Irms, Iripple):
        return (
            self.uC_losses()
            + self.IND_conduction_losses(Isource)
            + self.COND_conduction_losses(Iripple)
            + self.MOSFET_rpp_losses(Isource)
            + self.MOSFET_switching_losses(Irms)
            + self.PCB_conduction_losses(Irms)
            + self.SHUNT_conduction_losses(Irms)
            + self.MOSFET_conduction_losses(Irms)
            + self.LDO_losses()
        )

    def Psource(self, ISource):
        return self.Source_Resistance_losses(ISource)

    def Pcontacts(self, ILine):
        return self.Contact_Resistance_losses(ILine)

    def Source_Resistance_losses(self, ISource):
        return self.Rsource * ISource ** 2.0

    def Contact_Resistance_losses(self, ILine):
        return 3 * self.Rcable * ILine ** 2.0

    def MOSFET_rpp_losses(self, ISource):
        return self.Rrpp * ISource ** 2

    def MOSFET_conduction_losses(self, ILine):
        if self.controlAlgorithm == "foc":
            totalNumber = self.Ntransistors / 2.0
        else:
            totalNumber = self.Ntransistors / 3.0

        return (self.Rtransistor * ILine ** 2) * totalNumber

    def MOSFET_switching_losses(self, ILine):
        return (
            0.5 * self.Vdc * abs(ILine) * (self.tr + self.tf) * self.pwmFrequency
        ) * self.Ntransistors

    def COND_conduction_losses(self, Iripple):
        return self.Rcond * Iripple ** 2.0

    def IND_conduction_losses(self, ISource):
        return self.Rind * ISource ** 2.0

    def SHUNT_conduction_losses(self, ILine):
        return self.Rshunt * ILine ** 2.0

    def PCB_conduction_losses(self, ILine):
        return self.Rpcb * ILine ** 2.0

    def uC_losses(self):
        UuC = self.cc["Parts"]["Microcontroller"]["Supply Voltage (V)"]
        IuC = self.cc["Parts"]["Microcontroller"]["Supply Current (A)"]
        return UuC * IuC

    def LDO_losses(self):
        UuC = self.cc["Parts"]["Microcontroller"]["Supply Voltage (V)"]
        IuC = self.cc["Parts"]["Microcontroller"]["Supply Current (A)"]

        return (self.cc["Power Source"]["Supply Voltage (V)"] - UuC) * IuC

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {"Options": self.data["Options"], "Used": self.data["Used"]}
