def label = "mypod-${UUID.randomUUID().toString()}"
podTemplate(label: 'dockerbuild', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: dockerbuild
spec:
  containers:
    - name: docker
      image: docker
      command:
      - cat
      tty: true
      imagePullPolicy: Always
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
    node ('dockerbuild') {

      stage ('Build Dockerfile') {
        container('docker') {
          git url: 'https://github.com/s-lavr/jenkins-pipeline.git', branch: 'master'
          withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'f74f60fe-bc38-4b3e-ab91-d7af3416231e',
                            usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD']]) {

          sh '''
            docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
            docker build -t serglavr/hello .
            docker push serglavr/hello
          '''

          }
        }
      }


    }
}

podTemplate(label: 'deploytest', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: deploytest
  labels:
    some-label: some-label-value
spec:
  containers:
    - name: application
      image: serglavr/hello
      ports:
      - name: http-port
        containerPort: 80
    - name: curl
      image: appropriate/curl
      command:
      - cat
      tty: true
"""
) {
    node ('deploytest') {
      stage ('deploytest') {
        container('curl') {
        sh 'curl localhost:80'
        }
      }
    }
  }
