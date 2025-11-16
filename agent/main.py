import sys

from maa.agent.agent_server import AgentServer
from maa.toolkit import Toolkit

import my_action
import my_reco


def main():

    import custom

    try:
        Toolkit.init_option("./")
        socket_id = sys.argv[-1]
        AgentServer.start_up(socket_id)
        AgentServer.join()
        AgentServer.shut_down()

    except Exception as e:
        print(e)
        print("Agent启动失败！")


if __name__ == "__main__":
    main()
