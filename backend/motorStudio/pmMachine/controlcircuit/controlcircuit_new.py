import os
import math


class controlcircuit(object):
    """This model calculates the electronic losses of the ECU."""

    def __init__(self, data):

        self.data = data
        self.cc = self.data["Used"]
        self.temperature = self.cc.get("Temperature (C)", 25)
        self.controlAlgorithm = self.cc["control algorithm"]
        self.Nshunts = 1 if self.cc["current shunts"]["type"] == "single" else 2
        self.Ntransistors = self.cc["transistors"]["number"]
        self.Ninductors = self.cc["inductors"]["number"]
        self.Ncapacitors = self.cc["capacitors"]["number"]
        self.Nrpp = self.cc["reverse polarity protections"]["number"]
        self.tr = self.cc["transistors"]["component"]["Ton (s)"]
        self.tf = self.cc["transistors"]["component"]["Toff (s)"]
        self.ImaxTransistorRMS = self.cc["transistors"]["component"]["Current Rating RMS (A)"]
        self.pwmFrequency = self.cc["uC"]["component"]["PWM Frequency (Hz)"]
        self.dutyCycle = self.cc["uC"]["component"]["Duty Cycle (%)"]
        self.Vdc = self.cc["Supply Voltage (V)"]
        self.phaseAdvance = self.cc["Phase Advance (deg.el.)"]
        self.Cp = (self.cc["capacitors"]["component"]["Capacitance (F)"] * self.Ncapacitors)
        self.Ls = (self.cc["inductors"]["component"]["Inductance (H)"] * self.Ninductors)
        self.UuC = self.cc["uC"]["component"]["Supply Voltage (V)"]
        self.IuC = (self.cc["uC"]["component"]["Supply Current Max. (A)"] + self.cc["uC"]["component"]["Supply Current Nom. (A)"]) / 2

    def getLosses(self, Isource, Irms, Iripple):
        return {
            "Total Losses (W)": self.Psource(Isource) + self.Pcontacts(Irms) + self.PpowerStage(Isource, Irms, Iripple),
            "Additional Losses (W)": self.Psource(Isource) + self.PpowerStage(Isource, Irms, Iripple) - self.MOSFET_conduction_losses(Irms),
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
        Tc_Rtransistor = 0
        Rtransistor = self.cc["transistors"]["component"]["Resistance Curves"][0]["Resistance (Ohm)"][0]
        return Rtransistor * (1 + Tc_Rtransistor / 100 * (self.temperature - 25))

    @property
    def Rsource(self):
        return self.cc["Supply Resistance (Ohm)"]

    @property
    def Rcable(self):
        return self.cc["Cable Resistance (Ohm)"]

    @property
    def Rshunt(self):
        Tc_shunt = 0
        Rshunt = self.cc["current shunts"]["component"]["Resistance Curves"][0]["Resistance (Ohm)"][0]
        return Rshunt * (1 + Tc_shunt / 100 * (self.temperature - 25))

    @property
    def Rpcb(self):
        Tc_pcb = self.cc["pcb"]["component"]["Tc (%/C)"]
        Rpcb = self.cc["pcb"]["component"]["Resistance (Ohm)"]
        return Rpcb * (1 + Tc_pcb / 100 * (self.temperature - 25))

    @property
    def Rind(self):
        Tc_Ind = self.cc["inductors"]["component"]["Tc (%/C)"]
        Rind = self.cc["inductors"]["component"]
        return Rind * (1 + Tc_Ind / 100 * (self.temperature - 25))

    @property
    def Rrpp(self):
        Tc_rpp = 0
        Rrpp = self.cc["reverse polarity protections"]["component"]["Resistance Curves"][0]["Resistance (Ohm)"][0]
        return Rrpp * (1 + Tc_rpp / 100 * (self.temperature - 25))

    @property
    def Rcond(self):
        Tc_Cond = 0
        Rcond = self.cc["capacitors"]["component"]["Resistance Curves"][0]["Resistance (Ohm)"][0]
        return Rcond * (1 + Tc_Cond / 100 * (self.temperature - 25))

    def PpowerStage(self, Isource, Irms, Iripple):
        return (
            self.uC_losses()
            + self.IND_conduction_losses(Isource)
            + self.COND_conduction_losses(Iripple)
            + self.MOSFET_rpp_losses(Isource)
            + self.MOSFET_switching_losses(Irms)
            + self.MOSFET_conduction_losses(Irms)
            + self.PCB_conduction_losses(Irms)
            + self.SHUNT_conduction_losses(Irms)
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
        return (self.Rrpp * self.Nrpp) * ISource ** 2

    def MOSFET_conduction_losses(self, ILine):
        if self.controlAlgorithm == "foc":
            totalNumber = self.Ntransistors / 2.0
        else:
            totalNumber = self.Ntransistors / 3.0

        return (self.Rtransistor * ILine ** 2) * totalNumber

    def MOSFET_switching_losses(self, ILine):
        return (0.5 * self.Vdc * abs(ILine) * (self.tr + self.tf) * self.pwmFrequency) * self.Ntransistors

    def COND_conduction_losses(self, Iripple):
        return (self.Rcond * self.Ncapacitors) * Iripple ** 2.0

    def IND_conduction_losses(self, ISource):
        return (self.Rind * self.Ninductors) * ISource ** 2.0

    def SHUNT_conduction_losses(self, ILine):
        return (self.Rshunt * self.Nshunts) * ILine ** 2.0

    def PCB_conduction_losses(self, ILine):
        return self.Rpcb * ILine ** 2.0

    def uC_losses(self):
        return self.UuC * self.IuC

    def LDO_losses(self):
        return (self.Vdc - self.UuC) * self.IuC

    def reprJSON(self):
        """ Creates json representation of the object. """
        electronic = self.data["Used"]
        # Add to display the resistance values at the wanted temperature.
        # Resistance of this components is given as function of temperature.
        electronic["transistors"]["component"].update({
            "Resistance (Ohm)": self.Rtransistor
        })
        electronic["capacitors"]["component"].update({
            "Resistance (Ohm)": self.Rcond
        })
        electronic["reverse polarity protections"]["component"].update({
            "Resistance (Ohm)": self.Rrpp
        })

        return {
            "Options": self.data["Options"],
            "Used": electronic
        }
