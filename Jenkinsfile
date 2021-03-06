def label = "mypod-${BUILD_TAG}-${UUID.randomUUID().toString()}"

podTemplate(label: 'builddeploy', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: builddeploy
spec:
  # Use service account that can deploy to all namespaces
  serviceAccountName: jenkins
  containers:
    - name: helm
      image: alpine/helm:2.13.1
      command:
      - cat
      tty: true
    - name: docker
      image: docker
      command:
      - cat
      tty: true
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

  node ('builddeploy') {

    checkout(scm).each { k,v -> env.setProperty(k, v) }

    stage('Set correct image tag') {
      if (env.GIT_BRANCH == 'master') {
        env.IMAGE_TAG="${env.GIT_COMMIT}"
      }
      else if (env.TAG_NAME) {
        env.IMAGE_TAG="${env.TAG_NAME}"
      }
      else {
        env.IMAGE_TAG="${env.GIT_BRANCH}"
      }
    }

    stage ('Build application Dockerfile') {
      container('docker') {
        def build_result = sh(script: "docker build --no-cache -t serglavr/hello:${env.IMAGE_TAG} .", returnStatus: true)
        if (build_result == 0) {
          echo "Build is successful"
        }
        else {
          error("Build is not successful, exit code: $build_result")
        }
      }
    }

    stage ('Test application') {
      container('docker') {
        sh """
        docker network create --driver=bridge hello
        docker run -d --name=hello -e FLASKVERSION="${env.IMAGE_TAG}" --net=hello serglavr/hello:${env.IMAGE_TAG}
        """

        def tests = [:]
        tests["test_1"] = {test_curl_status()}
        tests["test_2"] = {test_curl_out()}

        parallel tests
      }
    }

    stage ('Push application') {
      container('docker') {
        if (env.CHANGE_ID == null) {
          withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'f74f60fe-bc38-4b3e-ab91-d7af3416231e',
                          usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD']]) {

            sh """
            docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
            """
          }

          def push_result = sh(script: "docker push serglavr/hello:${env.IMAGE_TAG}", returnStatus: true)
          if (push_result == 0) {
            echo "Push is successful"
          }
          else {
            error("Push is not successful, exit code: $push_result")
          }
        }
      }
    }

    stage ('Deploy helm chart') {
      if (env.GIT_BRANCH == 'master' || env.TAG_NAME) {
        container('helm') {

        // Copy credentials to helm container

          withCredentials([file(credentialsId: '60e080ad-f1b7-4e35-b4bb-077fc0124046', variable: 'KUBE')]) {
              sh """
              cp $KUBE ./kubeconfig
              """
          }

          sh "helm init --client-only"

        // Test if deploy is successful

          def deploy_result = sh (script: "helm upgrade test-release ./flask-server --set image.tag=${env.IMAGE_TAG} --install --wait --kubeconfig ./kubeconfig", returnStatus: true)
          if (deploy_result == 0) {
            echo "Deploy is successful"
          }
          else {
            error("Deploy is not successful, exit code: $deploy_result")
          }
        }
      }
    }
  }
}


// Functions

def test_curl_status() {
    def result = sh(script: 'docker run -i --net=hello appropriate/curl /usr/bin/curl hello:80', returnStatus: true)
        if (result == 0) {
          echo "Test completed successfully"
        }
        else {
          error("Test is not completed, error message: $result ")
        }
}

def test_curl_out() {
    def result = sh(script: 'docker run -i --net=hello appropriate/curl /usr/bin/curl hello:80', returnStdout: true)
        if (result.contains("${env.IMAGE_TAG}")) {
          echo "Test completed successfully"
        }
        else {
          error("Test is not completed")
        }
}
