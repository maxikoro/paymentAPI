# Payment Pet API

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [To Do](#todo)

## About <a name = "about"></a>

Создает композитный контейнер

## Getting Started <a name = "getting_started"></a>

### Prerequisites

Вам нужен установленный докер и гит.

### Installing

```
git clone https://github.com/maxikoro/paymentAPI.git
cd paymentAPI
docker compose up -d
```

## Usage <a name = "usage"></a>

### Postman collection
[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/15342782-f1b44bdd-3c15-45a9-a259-0e164f49a6da?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D15342782-f1b44bdd-3c15-45a9-a259-0e164f49a6da%26entityType%3Dcollection%26workspaceId%3D68c07b05-7bae-4c01-9e65-523859c05585)

### Архитектура
<img src="./PaymentPetArchitecture.png">

## To Do <a name = "todo"></a>
- Рефакторинг инициализации кафки(сейчас иногда она не успевает стартануть, не успевают создаться топики и сервисы валятся. Правда их можно отдельно зарестартить и вопрос решен :)
- Сделать кластер брокеров кафки(сейчас там один брокер, он же контроллер, без зуукипера) и поэксперементировать с отказами и последующей ребалансировкой
- Дед леттер кью(для полной картины надо имитировать, что некоторые платежи сразу не обрабатываются и продумать логику для этого)
- можно масштабировать микросервисы payment-service, updater-service.(просто накопировать их в докер-композе.ямл) Сейчас они по одному, можно увеличить до количества партиций в топиках(до 3)
