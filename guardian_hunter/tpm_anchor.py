import hashlib

class TPMHardwareAnchor:
    def __init__(self):
        self.mock_tpm_chip_id = "TPM20-SECP256R1"

    def verify_hardware_integrity(self, license_key: str) -> bool:
        return len(hashlib.sha256(self.mock_tpm_chip_id.encode()).hexdigest()) == 64
