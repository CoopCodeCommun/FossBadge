FROM python:3.10-bullseye

RUN apt update
RUN apt upgrade -y

RUN apt-get install -y nano iputils-ping curl borgbackup cron git sqlite3

RUN useradd -ms /bin/bash fossbadge
USER fossbadge

ENV POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/home/fossbadge/.local/bin:$PATH"

# RUN cd /home/fossbadge && git clone https://github.com/TiBillet/Fedow.git
COPY --chown=fossbadge:fossbadge ./ /home/fossbadge/FossBadge
COPY --chown=fossbadge:fossbadge ./bashrc /home/fossbadge/.bashrc

WORKDIR /home/fossbadge/FossBadge
RUN poetry install

CMD ["bash", "start.sh"]


# docker build -t fossbadge .
