# aws-eb-docker-django-skeleton


This is sample code.

Docker container with

* Python3
* Django1.10
* uwsgi
* nginx
* supervisor

Push to AWS EC2 Container Service, and deploy on ElasticBeanstalk.

[Japanese]

Django サンプルコード。

Docker イメージを作り、それを AWS EC2コンテナリポジトリ に Push し、
ElasticBeanstalk で そのコンテナを元にデプロイするまでのサンプルです。

ローカル環境に、docker-toolbox がインストールされている必要があります。

[Docker toolbox](https://www.docker.com/products/docker-toolbox)


fabric は、あらかじめローカル環境にインストールしておく必要があります。
おそらく、Python3 では動作しないため、ローカルの Python2 環境に
インストールする必要があります。

```
$ python
Python 2.7.10
...

$ sudo pip install fabric
```

## Dockerイメージのビルド


```
$ fab build
```
(もしくは $ docker build -t aws-eb-docker-django-skeleton )


## DBマイグレーション

```
$ fab manage:migrate
```

##  サーバ起動

```
$ fab up
```

(ポート 80, 443 をバインドします)


`$ docker-machine ls` でIPアドレスを調べ(例: 192.168.99.100 )、
ブラウザで開くと起動ページが見れます

```
$ open "http://192.168.99.100/"
```

## Docker リポジトリを、AWS EC2コンテナサービス (ECS) に登録する

プライベートリポジトリとして登録できます。

1. ローカルPCの AWS CLI を設定 (既に行っていれば不要)

1-1. IAM より、ローカルコンピュータに保存するログインクレデンシャルを作っておきます。
既に作ってある場合は不要です。

[IAMページ](https://console.aws.amazon.com/iam/home?region=ap-northeast-1#)

ユーザー → 新規ユーザーの作成

ユーザー名 適当に (例: aws-cli )

ユーザーのセキュリティ認証情報を表示 をクリックし、アクセスキー ID と シークレットアクセスキー を保存しておく。

もしくは「認証情報のダウンロード」を押して、CSVを保存しておく。

閉じる をクリック

作成したユーザーを選択し、「ポリシーのアタッチ」

**AmazonEC2ContainerRegistryFullAccess** をアタッチしておきましょう


1-2. aws cli のインストール

```
$ sudo pip install awscli --upgrade --ignore-installed six
```

1-3. aws を設定
```
$ aws configure
```

さきほどのクレデンシャル情報を入力しておく

```
AWS Access Key ID [None]: AK................
AWS Secret Access Key [None]: ********************************
Default region name [None]: ap-northeast-1
Default output format [None]:
```

2. AWS EC2 コンテナリポジトリの設定とイメージのプッシュ

2-1. AWS コンソールの ECSページを表示

[ECSページ](https://ap-northeast-1.console.aws.amazon.com/ecs/home?region=ap-northeast-1#/firstRun)

初回起動時、チェックボックスが出ます。

Store container images securely with Amazon ECR にチェックON して Continue。

Repository name にリポジトリ名を入力して、Next step。

すると、コンソールでの手順が表示されます。


2-2. ローカルでコンテナ登録コマンド実行

表示されたコマンドにそって

```
$ aws ecr get-login --region ap-northeast-1
```

ターミナルから入力すべきコマンドが表示されます。つまり、やるべきことは

```
$ $(aws ecr get-login --region ap-northeast-1)
```

です。

```
$ $(aws ecr get-login --region ap-northeast-1)
Flag --email has been deprecated, will be removed in 1.13.
Login Succeeded
```

fab のコマンドも用意してあります。
```
$ fab login_ecr
```

引き続き、AWSのページの手順に沿って続けます。
```
$ docker tag aws-eb-docker-django-skeleton:latest 000000000000.dkr.ecr.ap-northeast-1.amazonaws.com/aws-eb-docker-django-skeleton:latest
```

```
$ docker push 000000000000.dkr.ecr.ap-northeast-1.amazonaws.com/aws-eb-docker-django-skeleton:latest
```

fab のコマンドも用意してあります

```
$ fab push
```

3. プッシュしたイメージから ElasticBeanstalk でインスタンスを作成


3-1. EBを作成

[EB のページを表示](https://ap-northeast-1.console.aws.amazon.com/elasticbeanstalk/home?region=ap-northeast-1#/getting_started)

プラットフォームの選択 は、**Multi-container Docker** にして、「今すぐ起動」

(※起動する Docker コンテナは1つですが、単一Docker コンテナの設定ファイルと互換性が無いため、あとからコンテナを増やしたい場合等に困ります。マルチコンテナDockerで全く問題無いでしょう。(メモリ設定が必須で少し面倒なぐらい?))

そしたら、「初めての Elastic Beanstalk アプリケーション」という変なアプリケーションが
出来たので、これは無視して右上の「新しいアプリケーションの作成」をクリック

アプリケーション名は適当に、例: **aws-eb-docker-django-skeleton**

→ 次へ → ウェブサーバーの作成 →

プラットフォームの選択: **Multi-container Docker**

環境タイプ: 単一インスタンス

→ 次へ

送信元: **独自のアップロード**

今回は、手作業で Json ファイルをアップロードします。

本来は、S3経由でコマンドでアップロードなどした方が良いと思うのですが、
ここの ベストプラクティスはまだ確立できていません。(ebコマンドでできるか等もまだ不明…)

EC2コンテナサービス (ECS) を使う場合、Dockerrun.aws.json だけアップロードすれば良いです。

Dockerrun.aws.json のサンプルはこのリポジトリに含まれています。
image の箇所を修正した json ファイルを、「独自のアップロード」のファイルに指定します。

環境名、環境URL は、例: aws-eb-docker-django-skeleton を入力

その他のリソース は、今回は使わないのでチェック無しで「次へ」

構成の詳細は適当に。今回はテストなので t1.micro で充分です

環境タグ も不要なので入力せずに「次へ」

アクセス制限 も、そのままで『次へ」

内容がプレビューされますので、「起動」

しばらく待つとインスタンスが作られるのですが、そのままでは下記のようにエラーになります。

ECS task stopped due to: Essential container in task exited. (aws-eb-docker-django-skeleton: CannotPullContainerError: AccessDeniedException: User: arn:aws:sts::000000000000:assumed-role/aws-elasticbeanstalk-ec2-role/i-00000000 is not authorized to perform: ecr:GetAuthorizationToken on resource: * status code: 400, request id: 00000000-0000-0000)


3-2. ロールにポリシーを設定

エラーの原因は、EB のロールが ECS (コンテナレジストリ) の **GetAuthorizationToken** の
権限が無いためです。付与しましょう。

[IAM のロールページ](https://console.aws.amazon.com/iam/home?region=ap-northeast-1#roles)

から、**aws-elasticbeanstalk-ec2-role** を選択し、「**ポリシーのアタッチ**」→ container で検索して、

**AmazonEC2ContainerRegistryReadOnly** をアタッチします。


3-3. 再デプロイ

EB のアプリケーションのページの、アップロードとデプロイ → アプリケーションバージョン ページ

「最初のリリース」を選択して「デプロイ」

Environment update completed successfully. になりました。


4. ページ確認

EB には1つの URL が割り当てられます。例: aws-eb-docker-django-skeleton.ap-northeast-1.elasticbeanstalk.com

ブラウザでアクセスうするとページが表示されます。

