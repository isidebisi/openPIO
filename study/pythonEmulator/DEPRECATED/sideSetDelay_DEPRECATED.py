from dataclasses import dataclass

@dataclass
class SideSetDelayConfig:
    PINCTRL_SIDESET_COUNT: int  # Number of side-set bits
    EXECCTRL_SIDE_PINDIR: bool  # Whether side-set controls pindirs
    side_base_pin: int  # Base pin for side-set
    optional: bool  # Whether an optional bit is included
    pindirs: bool  # Whether side-set controls pindirs
    
    @property
    def SIDESET_COUNT(self):
        """Automatically calculates total side-set bits including optional bit."""
        return self.SIDESET_COUNT + (1 if self.optional else 0)

    @property
    def DELAY_COUNT(self):
        """Automatically calculates total delay bits including optional bit."""
        return 5 - self.SIDESET_COUNT
    
    @property
    def MAX_DELAY(self):
        """Calculates the maximum delay value."""
        return 2 ** self.DELAY_COUNT - 1

    @property
    def config_valid(self):
        """Checks if the configuration is valid."""
        if self.SIDESET_COUNT > 5 or self.SIDESET_COUNT < 0:
            return False
        if self.DELAY_COUNT > 8 or self.DELAY_COUNT < 0:
            return False
        if self.DELAY_COUNT + self.SIDESET_COUNT != 5:
            return False
        if self.side_base_pin < 0 or self.side_base_pin > 29:
            return False
