def label = "mypod-${UUID.randomUUID().toString()}"


podTemplate(label: 'buildtest', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: dockerbuild
spec:
  # Use service account that can deploy to all namespaces
  serviceAccountName: cd-jenkins
  containers:
    - name: helm
      image: alpine/helm
      command:
      - cat
      tty: true
    - name: curl
      image: appropriate/curl
      command:
      - cat
      tty: true
    - name: docker
      image: docker
      command:
      - cat
      tty: true
      # imagePullPolicy: Always
      env:
      - name: POD_IP
        valueFrom:
          fieldRef:
            fieldPath: status.podIP
      - name: DOCKER_HOST
        value: tcp://localhost:2375
    - name: dind
      image: docker:18.05-dind
      securityContext:
        privileged: true
      volumeMounts:
        - name: dind-storage
          mountPath: /var/lib/docker
  volumes:
    - name: dind-storage
      emptyDir: {}
"""
) {

  node ('buildtest') {
    checkout(scm).each { k,v -> env.setProperty(k, v) }

    stage('Set correct image tag') {
      if (env.GIT_BRANCH == 'master') {
        env.IMAGE_TAG="${env.GIT_BRANCH}-${env.GIT_COMMIT}"
      }
      else if (env.TAG_NAME) {
        env.IMAGE_TAG="${env.TAG_NAME}"
      }
      else {
        env.IMAGE_TAG="${env.GIT_BRANCH}"
      }
    }

    stage ('Build Dockerfile and push image') {
      container('docker') {
        sh """
        docker build --no-cache -t serglavr/hello:${env.IMAGE_TAG} .
        docker network create --driver=bridge hello
        docker run -d --name=hello --net=hello serglavr/hello:${env.IMAGE_TAG}
        docker run -i --net=hello appropriate/curl /usr/bin/curl hello:80
        """
        if (env.CHANGE_ID == null) {
          withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'f74f60fe-bc38-4b3e-ab91-d7af3416231e',
                          usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD']]) {

            sh """
            docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
            docker push serglavr/hello:${env.IMAGE_TAG}
            """

          }
        }
      }
    }

    stage ('Deploy helm chart') {
      if (env.GIT_BRANCH == 'master') {
        container('helm') {
          sh """
          helm version
          helm init --client-only
          helm upgrade test-release ./flask-server --set image.tag=${env.IMAGE_TAG} --install
          helm list
          """
        }
      }
    }
  }
}
