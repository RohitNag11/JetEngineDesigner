from ..flight_analyser.phase import Phase


class FlightAnalysis:
    def __init__(self, spec_heat_ratio=1.4, gas_const=287, density_sea=1.225, temp_sea=288.15, pressure_sea=101300):
        self.spec_heat_ratio = spec_heat_ratio
        self.gas_const = gas_const
        self.density_sea = density_sea
        self.temp_sea = temp_sea
        self.pressure_sea = pressure_sea
        self.phases: dict[str, Phase] = dict()

    def add_phase(self, phase_name, phase_conditions):
        phase = Phase(self.spec_heat_ratio,
                      self.gas_const,
                      self.density_sea,
                      self.temp_sea,
                      self.pressure_sea,
                      **phase_conditions)
        self.phases[phase_name] = phase
