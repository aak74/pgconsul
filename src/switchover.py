from .process import Process


class Switchover(Process):
    INIT = 'init'
    ELECTION = 'election'
    # CANDIDATE_FOUND = 'candidate_found'
    PROMOTE = 'promote'
    FINISH = 'finish'

    def __init__(self):
        super().__init__('switchover', [self.INIT, self.ELECTION, self.PROMOTE, self.FINISH])
        self.host_from = None
        self.host_to = None

    def to_dict(self) -> dict:
        result = super().to_dict()
        result.update(
            {
                "host_from": self.host_from,
                "host_to": self.host_to,
            }
        )
        return result
